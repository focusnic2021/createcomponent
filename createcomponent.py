#!/usr/bin/env python3.10
"""
навеяно - Генератор React компонентов на Python. Ускоряем создание TypeScript React компонентов с vim & python
https://www.youtube.com/watch?v=zU1kf3Qjtdk
"""
"""Хелпер для создания React компонентов.
Спрашивает, создаём компонент в components или pages 
(это две целевые директории с немного разными компонентами),
затем спрашивает, какой элемент создаём.

Если для pages элемент указываем MyComponent, создаст:
    pages/MyComponent/MyComponent.tsx
    pages/MyComponent/MyComponent.module.css
    pages/MyComponent/index.ts (опционально)

Если указать MyComponent/Element, создаст:
    pages/MyComponent/Element.tsx
    pages/MyComponent/Element.module.css
    pages/MyComponent/index.ts (опционально)
"""
from abc import abstractmethod, ABC
from dataclasses import dataclass
from pathlib import Path
# from typing import Literal, TypeAlias, Iterable

SRC_DIR = Path(__file__).parent / "src"

# BaseFolder: TypeAlias = Literal("components", "pages")


class Colors:
    HEADER = '\033|95m'
    OKBLUE = '\033|94m'
    OKCYAN = '\033|96m'
    OKGREEN = '\033|92m'
    WARNING = '\033|93m'
    FAIL = '\033|91m'
    ENDC = '\033|0m'
    BOLD = '\033|1m'
    UNDERLINE = '\033|4m'


@dataclass
class Element:
    full_path: Path  # директория для этого элемента
    name: str  # ниамменование этого элемента


class FileCreator(ABC):
    """класс наследует от абстрактного класса ABC.
    Его наследники будут реализовывать логику создания конкретных файлов."""

    def __init__(self, element: Element):
        self._element = element

    def create(self) -> None:
        """Creates empty file and then fill with contents"""
        # Создание директории, если она еще не создана и пустого файла:
        self._create_empty_file()
        # заполнение файла контентом:
        self._write_file_contents()

    def get_relative_filenames(self) -> str:
        """Returns relative filename as str for logging"""
        relative_path_start_index = 1 + len(str(SRC_DIR.resolve()))
        result = str(
            self.get_absolute_filename().resolve()
        )[relative_path_start_index:]
        return result

    def _create_empty_file(self):
        """Inint file if not exists"""
        self.get_absolute_filename().parent.mkdir(parents=True, exist_ok=True)
        self.get_absolute_filename().touch(exist_ok=True)

    @abstractmethod
    def get_absolute_filename(self) -> Path:
        """Returns file in Path format.
        Абстрактный метод. Его должен реализовать потомок этого класса"""
        pass

    @abstractmethod
    def _write_file_contents(self) -> None:
        """Fill file with contents.
        Абстрактный метод. Его должен реализовать потомок этого класса"""
        pass


class TSXFileCreator(FileCreator):
    """Element.tsx file creator"""
    def get_absolute_filename(self) -> Path:
        return self._element.full_path / (self._element.name + ".tsx")

    def _write_file_contents(self):
        self.get_absolute_filename().write_text(
            f"""import styles from "./{self._element.name}.module.css"

interface {self._element.name}Props {{

}}             

const {self._element.name} = ({{}}: {self._element.name}Props) => (
    <div>{self._element.name}</div>
)

export default {self._element.name}    
        """.strip())


class CSSFileCreator(FileCreator):
    """Element.module.css file creator"""
    def get_absolute_filename(self) -> Path:
        return self._element.full_path / (self._element.name + ".module.css")

    def _write_file_contents(self):
        pass


class IndexFileCreator(FileCreator):
    """Optional index.rs file creator"""
    def get_absolute_filename(self) -> Path:
        return self._element.full_path / "index.ts"

    def _write_file_contents(self):
        current_file_contents = self.get_absolute_filename().read_text()
        if current_file_contents.strip():
            return  # если файл пустой - выход из функции
        # ...иначе - дополнить строкой "export..."
        self.get_absolute_filename().write_text(
            f"""export {{default}} from "./{self._element.name}":"""
        )


class AskParams:
    """Ask params from user, parse it and create Element structure"""

    def __init__(self):
        self._element: Element  # в protector поле _element вложить тип данных Element

    def ask(self) -> Element:  # возвращает наружу этот самый Element
        """Ask all parameters - element folder and name"""
        base_folder = self._ask_base_folder()
        self._element = self._parse_as_element(
            self._ask_element(base_folder),
            base_folder
        )
        return self._element

    def _parse_as_element(self,
                          element_str: str,
                          base_folder) -> Element:  # base_folder: BaseFolder) -> Element:
        """распарсить имя элемента по его строковому представлению element_str.
        в список element_as_list вносятся последовательно все папки и подпапки,
        и собирается все это в relative_path.
        Наружу выдается сам Element с параметрами full_path и name"""
        element_as_list = element_str.split("/")
        element_name = element_as_list[-1]
        if len(element_as_list) > 1:
            # user entered: MyComponents/AuthorCourses
            relative_path = "/".join(element_as_list[:-1])
        else:
            # user entered: AuthorCourses
            relative_path = element_name
        return Element(
            full_path=SRC_DIR / base_folder / relative_path,
            name=element_name
        )

    def ask_ok(self, filenames) -> None: # def ask_ok(self, filenames: Iterable[str]) -> None:
        filenames = "\n\t".join(filenames)
        while True:
            print(f"\nИтак, создаем файлы:\n"
                  f"{Colors.HEADER}\t{filenames} {Colors.ENDC}\n\n")
            match_case = input("Ok? [Y]/N: ".strip().lower())
            if (match_case == "y" or match_case == ""):
                return
            elif match_case == "n":
                exit("Ок, выходим, ничего не создал.")
            else:
                print("Не понял, давай еще раз")

    def _ask_base_folder(self):   # def _ask_base_folder(self) -> BaseFolder:
        """Запрос пользователя - в какой директории будем создавать новый элемент.
        Реализовано через бесконечный цикл while_True - не выйдет, пока не ответит правильно"""
        while True:
            match_case = input("c - components, p - pages: ").strip().lower()
            if match_case == "c":
                return "components"
            elif match_case == "p":
                return "pages"
            else:
                print("Не понял, давай еще раз")

    def _ask_element(self, base_folder) -> str: # def _ask_element(self, base_folder: BaseFolder) -> str:
        """Возвращает имя элемента - совпадает с названием директории, куда помещаем"""
        return input(f"Куда кладём? {base_folder}/").strip()


class ElementFilesCreator:
    # класс управляет созданием конечных файлов.
    # Сам не создает, делегирует
    def __init__(self, element: Element):
        """конструктор класса.
        1) Принимает на вход element, которые сохраняется в protect-поле _element
        2) Создается пустой список _file_creators, элементами которого будут объекты класса FileCreator
        """
        self._element = element
        self._file_creators: list(FileCreator) = []

    def create(self):
        for file_creator in self._file_creators:
            file_creator.create()

    def register_file_creators(self, *file_creators: type(FileCreator)):
        for fc in file_creators:
            self._file_creators.append(fc(
                element=self._element
            ))

    def get_relative_filenames(self):    # def get_relative_filenames(self) -> tuple[str, ...]:
        return tuple(fc.get_relative_filenames() for fc in self._file_creators)


# точка входа:
def main():
    asker = AskParams()  # класс, реализующий запрос у пользователя параметров нового компонента
    element = asker.ask()

    # создается экземпляр класса ElementFilesCreator
    element_creator = ElementFilesCreator(element)
    # в котором регистрируются хендлеры
    element_creator.register_file_creators(
        TSXFileCreator,
        CSSFileCreator,
        IndexFileCreator
    )
    # запрос у пользователя - "Все ли нормально?Эти ли файлы создавать?"
    asker.ask_ok(element_creator.get_relative_filenames())
    element_creator.create()
    print("Все создал и весь такой молодец!")


# точка входа в приложение обернута в цикл проверки if __name__ == '__main__',
# чтобы в будущем можно было импортировать какие-то куски кода, на запуская логику всего приложения
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:  # это консольное приложение. При выходе из него через Cntr-D - чтобы не сыпались страшние сообщения
        pass

