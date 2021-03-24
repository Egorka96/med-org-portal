from dataclasses import dataclass

@dataclass
class InsurancePolicy:
    number: str

    @classmethod
    def get_from_dict(cls, data: dict) -> 'InsurancePolicy':
        return cls(
            number=data['number'],
        )


